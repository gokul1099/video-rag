
import json
import uuid
from datetime import datetime
from typing import Any,Dict, List, Optional
import instructor
import opik
from groq import Groq
from loguru import logger
from opik import Attachment, opik_context
import httpx

from kubrick_api import tools
from kubrick_api.agent.base_agent import BaseAgent
from kubrick_api.agent.groq.groq_tool import transform_tool_definition
from kubrick_api.agent.memory import MemoryRecord, Memory
from kubrick_api.config import get_settings
from kubrick_api.models import  (
    AssitantMessageResponse,
    GeneralResponseModel,
    RoutingResponseModel,
    VideoClipResponseModel
)

logger.bind(name="GroqAgent")
settings = get_settings()

class GroqAgent(BaseAgent):
    def __init__(self, name: str, mcp_server: str, memory: Optional[Memory] = None, disable_tools: list =None):
        super().__init__(
            name,
            mcp_server,
            memory,
            disable_tools
        )
        self.client = Groq(
            api_key=settings.GROQ_API_KEY,
            http_client=httpx.Client(trust_env=False)
        )
        self.instructor_client = instructor.from_groq(self.client, mode=instructor.Mode.JSON)
        self.thread_id = str(uuid.uuid4())
    
    async def _get_tools(self) -> List[Dict[str, Any]]:
        tools = await self.discover_tools()
        logger.info(f"{tools}")
        return [transform_tool_definition(tool) for tool in tools]
    
    @opik.track(name="build-chat-hitory")
    def _build_chat_history(
        self,
        system_prompt: str,
        user_message: str,
        session_id: int,
        image_base64: Optional[str] = None,
        n: int = settings.AGENT_MEMORY_SIZE,
    ) -> List[Dict[str, Any]] :
        history = [{"role" : "system", "content": system_prompt}]
        history += [{"role": record.role, "content": record.content} for record in self.memory.get_by_session_id(str(session_id), n)]

        user_content = (
            [
                {"type": "text", "text" : user_message},
                {
                    "type":"image_url",
                    "image_url": {"url": f"data:image/jpeg;base64, {image_base64}"}
                },
            ]
            if image_base64
            else user_message
        )

        history.append({"role": "user", "content": user_content})
        return history
    
    @opik.track(name="router", type="llm")
    def _should_use_tool(self,message: str) -> bool:
        messages = [
            {"role":"system", "content": self.routing_system_prompt},
            {"role":"user", "content": message}
        ]
        response = self.instructor_client.chat.completions.create(
            model=settings.GROQ_ROUTING_MODEL,
            response_model=RoutingResponseModel,
            messages= messages,
            max_completion_tokens = 20
        )

        return response.tool_use


    def validate_video_clip_response(self, video_clip_response: VideoClipResponseModel, video_clip_path: str) -> VideoClipResponseModel:
        """Validate the video clip response"""
        video_clip_response.clip_path = video_clip_path
        return video_clip_response
    
    async def _execute_tool_call(self, tool_call:Any, video_path: str, image_base64: str | None = None) -> str:
        logger.info(f"{tool_call}")
        function_name = tool_call.function.name
        function_args = json.loads(tool_call.function.arguments)
        function_args["video_path"] = video_path
        if function_name =="get_vidoe_clip_from_image":
            function_args["user_image"] = image_base64
        
        logger.info(f"Executing tool: {function_name} with args {function_args}")

        try:
            return await self.call_tool(function_name, function_args)
        except Exception as e:
            logger.error(f"Error executing tool {function_name}: {str(e)}")
            return f"Error executing tool {function_name}: {str(e)}"
    @opik.track(name="tool_use",type="tool")

    async def _run_with_tool(self, message:str , video_path:str, session_id: int, image_base64: str | None = None) -> str:
        """Execute chat completion with tool usage"""
        tool_use_system_prompt = self.tool_use_system_prompt.format(
            is_image_provided=bool(image_base64)
        )
        chat_history = self._build_chat_history(tool_use_system_prompt, message, session_id, image_base64=image_base64)
        logger.info(f"Logging self tools{self.tools}")

        response = (
            self.client.chat.completions.create(
                model=settings.GROQ_TOOL_USE_MODEL,
                messages=chat_history,
                tools=self.tools,
                tool_choice="auto",
                max_completion_tokens=4096
            )
            .choices[0]
            .message
        )
        tool_calls = response.tool_calls
        logger.info(f"Tool calls: {tool_calls}")

        if not tool_calls:
            logger.info(f"No tool calls available, returning general response...")
            return GeneralResponseModel(message=response.content)
        
        for tool_call in tool_calls:
            logger.info(f"Calling execute tool call {tool_call}")
            function_response = await self._execute_tool_call(tool_call, video_path, image_base64)
            logger.info(f"Function response: {function_response}")

            if tool_call.function.name == "get_video_clip_from_image":
                tool_response =f"This is the video context. Use it to answer the user's question: {function_response}"
            else:
                tool_response = function_response
            
            chat_history.append(
                {
                    "tool_call_id":tool_call.id,
                    "role":"tool",
                    "name": tool_call.function.name,
                    "content": tool_response
                }
            )

            response_model = (
                GeneralResponseModel if tool_call.function.name == "ask_question_about_video" else VideoClipResponseModel
            )
            logger.info(f"Chat history: {chat_history}")

            followup_response = self.instructor_client.chat.completions.create(
                model=settings.GROQ_TOOL_USE_MODEL,
                messages= chat_history,
                response_model=response_model
            )

            if isinstance(followup_response, VideoClipResponseModel):
                try:
                    logger.info("Validation VideoClip response")
                    self.validate_video_clip_response(followup_response, tool_response)

                    logger.info(f"Tracing image from trimmed clip: {followup_response.clip_path}")
                    first_image_path = tools.sample_first_frame(followup_response.clip_path)
                    opik_context.update_current_trace(
                        attachments=[
                            Attachment(
                                data=first_image_path,
                                content_type="image/png"
                            )
                        ]
                    )
                except ValueError as e:
                    logger.error(f"Failed to sample first frame from video: {e}")
            return followup_response
        

    @opik.track(name="generate-response", type="llm")
    def _response_general(self, message: str, session_id: int) -> GeneralResponseModel:
        chat_history = self._build_chat_history(self.general_system_prompt, message, session_id)
        response = self.instructor_client.chat.completions.create(
            model=settings.GROQ_GENERAL_MODEL,
            messages=chat_history,
            response_model=GeneralResponseModel
        )
        return response
    def _add_to_memory(self,role: str, content: str, session_id: int ,user_id:int) -> None:
        """Add a message to the agent's memory"""
        self.memory.insert(
            MemoryRecord(
                message_id=str(uuid.uuid4()),
                role=role,
                content=content,
                timestamp=datetime.now(),
                session_id=str(session_id),
            )
        )
    
    @opik.track(name="memory-insertion", type="general")
    def _add_memory_pair(self, user_message: str, assitant_message:str, session_id, user_id) -> None:
        self._add_to_memory("user",user_message, session_id, user_id)
        self._add_to_memory("assistant", assitant_message, session_id, user_id)
    
    @opik.track(name="chat", type="general")
    async def chat(
        self,
        message: str,
        session_id: int,
        user_id: int,
        video_path: Optional[str] = None,
        image_base64: Optional[str] = None,
    ) -> AssitantMessageResponse:
        """Main entry point for processing a user message"""
        opik_context.update_current_trace(thread_id=self.thread_id)
        
        tool_required = video_path and self._should_use_tool(message)
        logger.info(f"Tool required: {tool_required}")

        if tool_required:
            response = await self._run_with_tool(message, video_path, session_id, image_base64)
        else:
            logger.info("Running general response")
            response = self._response_general(message, session_id)
        
        self._add_memory_pair(message, response.message, session_id, user_id)

        return AssitantMessageResponse(**response.dict())
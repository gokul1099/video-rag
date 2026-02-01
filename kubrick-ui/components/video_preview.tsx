import React from 'react';

interface VideoPreviewProps {
    uri: string;
}

export const VideoPreview: React.FC<VideoPreviewProps> = ({ uri }) => {
    return (
        <div className="w-full">
            <video className="w-full rounded-base" controls>
                <source src={uri} type="video/mp4" />
                Your browser does not support the video tag.
            </video>
        </div>
    );
};
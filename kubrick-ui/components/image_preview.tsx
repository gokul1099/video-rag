import React, { useState } from 'react';

interface ImagePreviewProps {
    uri: string;
    alt?: string;
    width?: number;
    height?: number;
    className?: string;
}

export const ImagePreview: React.FC<ImagePreviewProps> = ({
    uri,
    alt = 'Preview',
    width = 200,
    height = 200,
    className = '',
}) => {
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    return (
        <div className={`image-preview-container ${className}`}>
            {isLoading && <div className="skeleton-loader" />}
            {error && <div className="error-message">{error}</div>}
            <img
                src={uri}
                alt={alt}
                width={width}
                height={height}
                onLoad={() => setIsLoading(false)}
                onError={() => {
                    setIsLoading(false);
                    setError('Failed to load image');
                }}
                style={{ display: isLoading ? 'none' : 'block' }}
            />
        </div>
    );
};
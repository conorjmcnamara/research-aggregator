import React, { FC } from 'react';

export const Home: FC = () => {
    return (
        <div className="default-display-container">
            <h1>Welcome</h1>
            <p>Explore the latest areas of computer science research by topic and search query.<br />
            Click a research paper entry to show its abstract, topic areas and source.<br />
            Create an account or login to view bookmarked papers.</p>
        </div>
    );
}
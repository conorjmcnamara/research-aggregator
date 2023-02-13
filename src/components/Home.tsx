import React, { FC } from 'react';

export const Home: FC = () => {
    return (
        <div className="home">
            <h1 className="home-title">Welcome</h1>
            <p className="home-text">Explore the latest areas of computer science research by topic and search query.<br />
            Click a research paper entry to show its abstract, topic codes and source</p>
        </div>
    );
}
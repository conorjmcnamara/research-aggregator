import React, { FC, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { topicsI } from '../utils/utils';

interface Props {
    topics: topicsI
}

export const Navigation: FC<Props> = ({topics}) => {
    const [query, setQuery] = useState<string>("");
    const navigate = useNavigate();
    const topicID: string[] = Object.keys(topics);

    return (
        <div>
            <header className="header">
                <h1 className="header-title" onClick={() => navigate(`/`)}>Computer Science Research</h1>

                {/* display a search bar with navigation to /search/$id */}
                <div className='header-search-bar'>
                    <input placeholder="Search papers" onChange={event => setQuery(event.target.value)} />
                </div>
                <button onClick={() => navigate(`/search/${query}`)}>Search</button>

                <button className="header-bookmarks">Bookmarks</button>
                <button className="header-sign-in">Sign In</button>
            </header>

            <div className="navigation-container">
                <div className="navigation-buttons">
                    <h1 className="navigation-topic-title">Topics</h1>

                    <div className="navigation-desktop-buttons">
                        {/* display topic buttons with navigation to /topic/$id */}
                        {topicID.map((id: string) => (
                            <button key={`${id}btn`} onClick={() => navigate(`/topic/${id}`)}>{topics[id]}</button>
                        ))}
                    </div>

                    <div className="navigation-mobile-buttons">
                        <select>
                            <option selected disabled hidden>Select a topic</option>
                            {topicID.map((id: string) => (
                                <option key={`${id}btn`} value={id}>{topics[id]}</option>
                            ))}
                        </select>
                    </div>
                </div>
            </div>
        </div>
    );
}
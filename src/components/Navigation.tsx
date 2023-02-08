import React, { FC, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { topicsI } from '../utils/utils';

interface Props {
    topics: topicsI
}

export const Navigation: FC<Props> = ({topics}) => {
    const [query, setQuery] = useState("");
    const navigate = useNavigate();
    const topicID: string[] = Object.keys(topics);

    return (
        <div>
            {/* display topic buttons with navigation to /topic/$id */}
            {topicID.map((id: string) => (
                <button key={`${id}btn`} onClick={() => navigate(`/topic/${id}`)}>{topics[id]}</button>
            ))}

            {/* display a search bar with navigation to /search/$id */}
            <input placeholder="Enter a search query..." onChange={event => setQuery(event.target.value)} />
            <button onClick={() => navigate(`/search/${query}`)}>Search</button>
        </div>
    );
}
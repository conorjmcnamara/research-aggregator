import React, { FC, useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { topicsI, dbDataI } from '../utils/utils';

interface Props {
    topics: topicsI
}

export const DisplayTopic: FC<Props> = ({topics}) => {
    // get the topic ID from the URL parameter
    let {id} = useParams<{id: string}>();
    id ??= "";
    
    let validID: boolean = true;
    if (!topics[id]) {
        validID = false;
    }

    // fetch data from the Flask API given a topic ID
    const [topicData, setTopicData] = useState<dbDataI[]>();
    useEffect(() => {
        // avoid requesting data with a known invalid topic ID
        if (validID) {
            fetch(`/topic-query/${id}`).then(res => res.json()).then(data => {
                setTopicData(data);
            });
        }
    }, [id, validID]);
   
    // invalid topic ID
    if (!validID) {
        return (
            <p>Invalid topic ID: '{id}'</p>
        )
    }
    // loading
    else if (!topicData) {
        return (
            <p>Loading...</p>
        )
    }
    return (
        <div>
            <h1>{id}: {topics[id]}</h1>

            {/* display research papers given the passed topic ID */}
            {topicData.map((paper: dbDataI, i: number) => (
                <>
                <h1 key={`title${i}`}>{paper.title}</h1>
                <p key={`url${i}`}>{paper.url}</p>
                <p key={`date${i}`}>{paper.date}</p>
                <p key={`summary${i}`}>{paper.abstract}</p>
                <p key={`source${i}`}>{paper.source}</p>

                {/* display the authors */}
                {paper.authors.map((author: string, j: number) => (
                    <p key={`author${i}${j}`}>{author}</p>
                ))}
                </>
            ))}
        </div>
    );
}
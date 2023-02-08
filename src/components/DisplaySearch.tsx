import React, { FC, useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { topicsI, dbDataI } from '../utils/utils';

interface Props {
    topics: topicsI
}

export const DisplaySearch: FC<Props> = ({topics}) => {
    // get the search query from the URL parameter
    let {query} = useParams<{query: string}>();
    query??= "";

    // fetch data from the Flask API given a search query
    const [queryData, setQueryData] = useState<dbDataI[]>();
    useEffect(() => {
        fetch(`/search-query/${query}`).then(res => res.json()).then(data => {
            setQueryData(data);
        });
    }, [query]);
    
    // check that search query data exists
    if (queryData) {
        // ensure the response is not empty
        if (queryData.length === 0) {
            return (
                <p>No data found with the search query: '{query}'</p>
            )
        }
        return (
            <div>
                {/* display research papers given the passed search */}
                {queryData.map((paper: dbDataI, i: number) => (
                    <>
                    <h1 key={`title${i}`}>{paper.title}</h1>
                    <p key={`topic${i}`}>{paper.topic}: {topics[paper.topic]}</p>
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
        )
    }
    // loading
    return (
        <p>Loading...</p>
    );
}
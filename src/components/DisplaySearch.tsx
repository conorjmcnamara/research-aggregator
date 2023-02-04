import React, { FC, useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { topicsI } from '../utils/topics';

interface Props {
    topics: topicsI
}

export const DisplaySearch: FC<Props> = ({topics}) => {
    // get the search query from the URL parameter
    let {query} = useParams<{query: string}>();
    query??= "";

    interface queryDataI {
        topic: string;
        web_url: string;
        date: string;
        title: string;
        summary: string;
        authors: string[];
        pdf_url: string;
    }

    // fetch data from the Flask API given a search query
    const [queryData, setQueryData] = useState<queryDataI[]>();
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
                {queryData.map((paper: queryDataI, i: number) => (
                    <>
                    <h1 key={`title${i}`}>{paper.title}</h1>
                    <p key={`topic${i}`}>{paper.topic}: {topics[paper.topic]}</p>
                    <p key={`web_url${i}`}>{paper.web_url}</p>
                    <p key={`pdf_url${i}`}>{paper.pdf_url}</p>
                    <p key={`date${i}`}>{paper.date}</p>
                    <p key={`summary${i}`}>{paper.summary}</p>

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
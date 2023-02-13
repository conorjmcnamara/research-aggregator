import React, { FC, useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { topicsI, dbDataI, showHiddenI } from '../utils/utils';

interface Props {
    topics: topicsI
}

export const DisplayTopic: FC<Props> = ({topics}) => {
    let {id} = useParams<{id: string}>();
    id ??= "";
    
    let validID: boolean = true;
    if (!topics[id]) {
        validID = false;
    }

    // fetch data from the Flask API given a topic ID
    const [topicData, setTopicData] = useState<dbDataI[]>();
    useEffect(() => {
        if (validID) {
            fetch(`/topic-query/${id}`).then(response => response.json()).then(data => {
                setTopicData(data);
            });
        }
    }, [id, validID]);

    // display a paper's abstract, topics and source
    const [showHidden, setShowHidden] = useState<showHiddenI>({});
    const toggleHidden = (index: string) => {
        setShowHidden(prevShowHidden => ({
            [index]: !prevShowHidden[index]
        }));
    }

    // check for an invalid topic ID
    if (!validID) {
        return (
            <h1 className="info-h1">Invalid topic ID: {id}</h1>
        )
    }
    // loading
    else if (!topicData) {
        return (
            <h1 className="info-h1">Loading...</h1>
        )
    }
    return (
        <div className="research-data">
            <h1>Topic: {topics[id]}</h1>

            <table cellSpacing="0" cellPadding="0">
                {topicData.map((paper: dbDataI, i: number) => (
                    <>
                    <tr>
                        <td className="research-title-col" onClick={() => toggleHidden(`topic${id}${i}`)}>
                            <h2 key={`title${i}`}><a className="research-paper-title" href={paper.url}>{paper.title}</a></h2>
                        </td>
                        <td className="research-bookmark-col">
                            <h3>Bookmark</h3>
                        </td>
                    </tr>

                    <tr onClick={() => toggleHidden(`topic${id}${i}`)}>
                        <td className="research-author-col" colSpan={2} >
                            {paper.authors.map((author: string, j: number) => (
                                <span key={`author${i}${j}`}>{(j ? ", " : "") + author}</span>
                            ))}
                            <p>{paper.date}</p>
                        </td>
                    </tr>
                        
                    <tr onClick={() => toggleHidden(`topic${id}${i}`)}>
                        <td className="research-hidden-col" colSpan={2} style={{display: showHidden[`topic${id}${i}`] ? "table-cell" : "none"}}>
                            <p className="research-paper-abstract">{paper.abstract}</p>
                            <p className="research-paper-topic"><b>Topics:</b> {paper.topic}</p>
                            <p className="research-paper-source"><b>Source:</b> {paper.source}</p>
                        </td>
                    </tr>
                    </>
                ))}
            </table>
        </div>
    );
}
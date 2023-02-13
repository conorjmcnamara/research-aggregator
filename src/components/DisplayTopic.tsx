import React, { FC, useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { topicsI, dbDataI, showHiddenI } from '../utils/utils';

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

    // display a paper's abstract, topics and source
    const [showHidden, setShowHidden] = useState<showHiddenI>({});
    const toggleHidden = (index: string) => {
        setShowHidden(prevShowHidden => ({
            [index]: !prevShowHidden[index]
        }));
    }

    // invalid topic ID
    if (!validID) {
        return (
            <h1 style={{ textAlign: "center"}}>Invalid topic ID: {id}</h1>
        )
    }
    // loading
    else if (!topicData) {
        return (
            <h1 style={{ textAlign: "center"}}>Loading...</h1>
        )
    }
    return (
        <div className="research-data">
            <h1 className="research-selected-query">Topic: {topics[id]}</h1>

            <table cellSpacing="0" cellPadding="0">
                {/* display research papers given the passed topic ID */}
                {topicData.map((paper: dbDataI, i: number) => (
                    <>
                    <tr>
                        <td className="research-title-row" onClick={() => toggleHidden(`topic${id}${i}`)}>
                            <h2 key={`title${i}`}><a className={"research-title"} href={paper.url}>{paper.title}</a></h2>
                        </td>

                        <td className="research-bookmark-row">
                            <p className="research-bookmark">Bookmark</p>
                        </td>
                    </tr>

                    <tr onClick={() => toggleHidden(`topic${id}${i}`)}>
                        <td colSpan={2} className="research-author-row">
                            {/* display the authors */}
                            {paper.authors.map((author: string, j: number) => (
                                <span key={`author${i}${j}`} className="research-author">
                                    { (j ? ', ' : '') + author}
                                </span>
                            ))}
                            <p className="research-date">{paper.date}</p>
                        </td>
                    </tr>
                        
                    <tr onClick={() => toggleHidden(`topic${id}${i}`)}>
                        <td style={{ display: showHidden[`topic${id}${i}`] ? 'table-cell' : 'none'}} colSpan={2} className="research-hidden-row">
                            <p className="research-abstract">{paper.abstract}</p>
                            <p className="research-abstract">Topics: {paper.topic}</p>
                            <p className="research-abstract">Source: {paper.source}</p>
                        </td>
                    </tr>
                    </>
                ))}
            </table>
        </div>
    );
}
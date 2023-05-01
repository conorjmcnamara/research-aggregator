import React, { FC, useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { researchDataI, showHiddenI, getCookie, topics } from '../utils/utils';

export const DisplayTopic: FC = () => {
    const [topicData, setTopicData] = useState<researchDataI>({});
    const [paperUIDs, setPaperUIDs] = useState<string[]>();
    const [showHidden, setShowHidden] = useState<showHiddenI>({});
    var doubleSubmitToken: string | undefined = getCookie("csrf_access_token");
    var validID: boolean = true;
    var {id} = useParams<{id: string}>();
    id ??= "";
    
    if (!topics[id]) {
        validID = false;
    }

    useEffect(() => {
        if (!validID) return;
        fetch(`/api/topic/${id}`)
        .then(response => response.json()).then(data => {
            setTopicData(data);
            setPaperUIDs(Object.keys(data));
        })
        .catch((error) => {
            console.log(error.message);
        });
    }, [id, validID]);

    // display a paper's abstract, topics and source
    const toggleHidden = (index: string) => {
        setShowHidden(prevShowHidden => ({
            [index]: !prevShowHidden[index]
        }));
    }

    const bookmarkPaper = async(uid: string) => {
        if (!doubleSubmitToken || !topicData) return;
        const requestOptions = {
            method: "POST",
            headers: {"Content-Type": "application/json",
            "X-CSRF-TOKEN": doubleSubmitToken},
            body: JSON.stringify({uid: uid})
        }
        fetch("/api/bookmarks", requestOptions)
        .catch((error) => {
            console.log(error.message);
        });
    }

    if (!validID) {
        return (<h1 className="info-h1">Invalid topic ID: {id}</h1>);
    }
    else if (!topicData || !paperUIDs) {
        return (<h1 className="info-h1">Loading...</h1>);
    }
    return (
        <div className="research-data">
            <h1>Topic: {topics[id]}</h1>
            <table cellSpacing="0" cellPadding="0">
                {paperUIDs.map((uid: string, i: number) => (
                    <>
                    <tr>
                        <td className="research-title-col" onClick={() => toggleHidden(`topic${id}${i}`)}>
                            <h2 key={`title${i}`}><a className="research-paper-title" href={topicData[uid].url}>{topicData[uid].title}</a></h2>
                        </td>
                        <td className="research-bookmark-col"><h3 onClick={() => bookmarkPaper(`${topicData[uid]._id}`)}>Bookmark</h3></td>
                    </tr>

                    <tr onClick={() => toggleHidden(`topic${id}${i}`)}>
                        <td className="research-author-col" colSpan={2} >
                            {topicData[uid].authors.map((author: string, j: number) => (
                                <span key={`author${i}${j}`}>{(j ? ", " : "") + author}</span>
                            ))}
                            <p>{topicData[uid].date}</p>
                        </td>
                    </tr>
                        
                    <tr onClick={() => toggleHidden(`topic${id}${i}`)}>
                        <td className="research-hidden-col" colSpan={2} style={{display: showHidden[`topic${id}${i}`] ? "table-cell" : "none"}}>
                            <p className="research-paper-abstract">{topicData[uid].abstract}</p>
                            <p className="research-paper-topic"><b>Topics:</b> {topics[topicData[uid].topic]} ({topicData[uid].topic})</p>
                            <p className="research-paper-source"><b>Source:</b> {topicData[uid].source}</p>
                        </td>
                    </tr>
                    </>
                ))}
            </table>
        </div>
    );
}
import React, { FC, useState, useEffect } from 'react';
import { researchDataI, showHiddenI, getCookie, topics } from '../utils/utils';

export const Bookmarks: FC = () => {
    const [bookmarkData, setBookmarkData] = useState<researchDataI>({});
    const [paperUIDs, setPaperUIDs] = useState<string[]>();
    const [showHidden, setShowHidden] = useState<showHiddenI>({});
    var doubleSubmitToken: string | undefined = getCookie("csrf_access_token");

    useEffect(() => {
        if (!doubleSubmitToken) return;
        const requestOptions = {
            method: "GET",
            headers: {"Content-Type": "application/json"}
        }
        fetch(`/api/bookmarks`, requestOptions)
        .then(response => response.json()).then(data => {
            setBookmarkData(data);
            setPaperUIDs(Object.keys(data));
        })
        .catch((error) => {
            console.log(error);
        });
    }, [doubleSubmitToken]);

    // display a paper's abstract, topics and source
    const toggleHidden = (index: string) => {
        setShowHidden(prevShowHidden => ({
            [index]: !prevShowHidden[index]
        }));
    }

    const removePaper = async(uid: string) => {
        if (!doubleSubmitToken || !bookmarkData) return;
        const requestOptions = {
            method: "DELETE",
            headers: {"Content-Type": "application/json",
            "X-CSRF-TOKEN": doubleSubmitToken},
            body: JSON.stringify({uid: uid})
        }
        fetch("/api/bookmarks", requestOptions)
        .then(response => {
            if (response.status === 200) {
                delete bookmarkData[uid];
                setPaperUIDs(Object.keys(bookmarkData));
            }
        })
        .catch((error) => {
            console.log(error);
        });
    }

    if (!doubleSubmitToken) {
        return (<h1 className="info-h1">Create an account or login to view bookmarked papers</h1>);
    }
    else if (!bookmarkData || !paperUIDs) {
        return (<h1 className="info-h1">Loading...</h1>);
    }
    else if (paperUIDs.length === 0) {
        return (<h1 className="info-h1">Your bookmarked papers will be displayed here</h1>);
    }
    return (
        <div className="research-data">
            <h1>Bookmarks</h1>
            <table cellSpacing="0" cellPadding="0">
                {paperUIDs.slice(0).reverse().map((uid: string, i: number) => (
                    <>
                    <tr>
                        <td className="research-title-col" onClick={() => toggleHidden(`bookmark${i}`)}>
                            <h2 key={`title${i}`}><a className="research-paper-title" href={bookmarkData[uid].url}>{bookmarkData[uid].title}</a></h2>
                        </td>
                        <td className="research-bookmark-col"><h3 onClick={() => removePaper(`${bookmarkData[uid]._id}`)}>Unsave</h3></td>
                    </tr>

                    <tr onClick={() => toggleHidden(`bookmark${i}`)}>
                        <td className="research-author-col" colSpan={2} >
                            {bookmarkData[uid].authors.map((author: string, j: number) => (
                                <span key={`author${i}${j}`}>{(j ? ", " : "") + author}</span>
                            ))}
                            <p>{bookmarkData[uid].date}</p>
                        </td>
                    </tr>
                        
                    <tr onClick={() => toggleHidden(`bookmark${i}`)}>
                        <td className="research-hidden-col" colSpan={2} style={{display: showHidden[`bookmark${i}`] ? "table-cell" : "none"}}>
                            <p className="research-paper-abstract">{bookmarkData[uid].abstract}</p>
                            <p className="research-paper-topic"><b>Topics:</b> {topics[bookmarkData[uid].topic]} ({bookmarkData[uid].topic})</p>
                            <p className="research-paper-source"><b>Source:</b> {bookmarkData[uid].source}</p>
                        </td>
                    </tr>
                    </>
                ))}
            </table>
        </div>
    );
}
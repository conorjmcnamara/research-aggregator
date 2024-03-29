import React, { FC, useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { useSelector } from 'react-redux';
import { RootState } from '../store';
import { researchDataI, showHiddenI, topics } from '../utils/utils';

export const DisplaySearch: FC = () => {
    const [searchData, setSearchData] = useState<researchDataI>({});
    const [paperUIDs, setPaperUIDs] = useState<string[]>();
    const [showHidden, setShowHidden] = useState<showHiddenI>({});
    var loginCookie = useSelector((state: RootState) => state.loginCookie.cookie);
    var {query} = useParams<{query: string}>();
    query ??= "";

    useEffect(() => {
        fetch(`/api/search/${query}`)
        .then(response => response.json()).then(data => {
            setSearchData(data);
            setPaperUIDs(Object.keys(data));
        })
        .catch((error) => {
            console.log(error.message);
        });
    }, [query]);

    // display a paper's abstract, topics and source
    const toggleHidden = (index: string) => {
        setShowHidden(prevShowHidden => ({
            [index]: !prevShowHidden[index]
        }));
    }

    const bookmarkPaper = async(uid: string) => {
        if (!loginCookie || !searchData) return;
        const requestOptions = {
            method: "POST",
            headers: {"Content-Type": "application/json",
            "X-CSRF-TOKEN": loginCookie},
            body: JSON.stringify({uid: uid})
        }
        fetch("/api/bookmarks", requestOptions)
        .catch((error) => {
            console.log(error.message);
        });
    }

    if (!searchData || !paperUIDs) {
        return (<h1 className="info-h1">Loading...</h1>);
    }
    else if (paperUIDs.length === 0) {
        return (<h1 className="info-h1">No data found with the search query: {query}</h1>);
    }
    return (
        <div className="research-data">
            <h1 className="research-query">Search: {query}</h1>
            <table cellSpacing="0" cellPadding="0">
                {paperUIDs.map((uid: string, i: number) => (
                    <React.Fragment>
                        <tr>
                            <td className="research-title-col" onClick={() => toggleHidden(`search${searchData[uid].url}${i}`)}>
                                <h2 key={`title${i}`}><a className="research-paper-title" href={searchData[uid].url}>{searchData[uid].title}</a></h2>
                            </td>
                            <td className="research-bookmark-col"><h3 onClick={() => bookmarkPaper(`${searchData[uid]._id}`)}>Bookmark</h3></td>
                        </tr>

                        <tr onClick={() => toggleHidden(`search${searchData[uid].url}${i}`)}>
                            <td className="research-author-col" colSpan={2}>
                                {searchData[uid].authors.map((author: string, j: number) => (
                                    <span key={`author${i}${j}`}>{(j ? ", " : "") + author}</span>
                                ))}
                                <p>{searchData[uid].date}</p>
                            </td>
                        </tr>
                            
                        <tr onClick={() => toggleHidden(`search${searchData[uid].url}${i}`)}>
                            <td className="research-hidden-col" colSpan={2} style={{display: showHidden[`search${searchData[uid].url}${i}`] ? "table-cell" : "none"}}>
                                <p className="research-paper-abstract">{searchData[uid].abstract}</p>
                                <p className="research-paper-topic">
                                    <b>Topics: </b>
                                    <React.Fragment>
                                        {searchData[uid].topics.map((topic: string, k: number) => (
                                            <span key={`topic${i}${k}`}>{(k ? ", " : "") + topic}</span>
                                        ))}
                                    </React.Fragment>
                                </p>
                                <p className="research-paper-source"><b>Source:</b> {searchData[uid].source}</p>
                            </td>
                        </tr>
                    </React.Fragment>
                ))}
            </table>
        </div>
    );
}
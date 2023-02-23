import React, { FC, useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { topicsI, researchDataI, showHiddenI } from '../utils/utils';

interface Props {
    topics: topicsI
}

export const DisplaySearch: FC<Props> = ({topics}) => {
    let {query} = useParams<{query: string}>();
    query??= "";

    const [queryData, setQueryData] = useState<researchDataI[]>();
    useEffect(() => {
        fetch(`/api/search/${query}`).then(response => response.json()).then(data => {
            setQueryData(data);
        });
    }, [query]);

    // display a paper's abstract, topics and source
    const [showHidden, setShowHidden] = useState<showHiddenI>({});
    const toggleHidden = (index: string) => {
        setShowHidden(prevShowHidden => ({
            [index]: !prevShowHidden[index]
        }));
    }

    if (!queryData) {
        return (<h1 className="info-h1">Loading...</h1>);
    }
    else if (queryData.length === 0) {
        return (<h1 className="info-h1">No data found with the search query: {query}</h1>);
    }
    return (
        <div className="research-data">
            <h1 className="research-query">Search: {query}</h1>
            <table cellSpacing="0" cellPadding="0">
                {queryData.map((paper: researchDataI, i: number) => (
                    <>
                    <tr>
                        <td className="research-title-col" onClick={() => toggleHidden(`search${paper.topic}${i}`)}>
                            <h2 key={`title${i}`}><a className="research-paper-title" href={paper.url}>{paper.title}</a></h2>
                        </td>
                        <td className="research-bookmark-col"><h3>Bookmark</h3></td>
                    </tr>

                    <tr onClick={() => toggleHidden(`search${paper.topic}${i}`)}>
                        <td className="research-author-col" colSpan={2}>
                            {paper.authors.map((author: string, j: number) => (
                                <span key={`author${i}${j}`}>{(j ? ", " : "") + author}</span>
                            ))}
                            <p>{paper.date}</p>
                        </td>
                    </tr>
                        
                    <tr onClick={() => toggleHidden(`search${paper.topic}${i}`)}>
                    <td className="research-hidden-col" colSpan={2} style={{display: showHidden[`search${paper.topic}${i}`] ? "table-cell" : "none"}}>
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
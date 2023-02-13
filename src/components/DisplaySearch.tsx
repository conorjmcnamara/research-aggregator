import React, { FC, useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { topicsI, dbDataI, showHiddenI } from '../utils/utils';

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

    // display a paper's abstract, topics and source
    const [showHidden, setShowHidden] = useState<showHiddenI>({});
    const toggleHidden = (index: string) => {
        setShowHidden(prevShowHidden => ({
            [index]: !prevShowHidden[index]
        }));
    }
    
    // check that search query data exists
    if (queryData) {
        // ensure the response is not empty
        if (queryData.length === 0) {
            return (
                <h1 style={{ textAlign: "center"}}>No data found with the search query: {query}</h1>
            )
        }
        return (
            <div className="research-data">
                <h1 className="research-selected-query">Search: {query}</h1>

                <table cellSpacing="0" cellPadding="0">
                    {/* display research papers given the passed topic ID */}
                    {queryData.map((paper: dbDataI, i: number) => (
                        <>
                        <tr>
                            <td className="research-title-row" onClick={() => toggleHidden(`search${paper.topic}${i}`)}>
                                <h2 key={`title${i}`}><a className={"research-title"} href={paper.url}>{paper.title}</a></h2>
                            </td>

                            <td className="research-bookmark-row">
                                <p className="research-bookmark">Bookmark</p>
                            </td>
                        </tr>

                        <tr onClick={() => toggleHidden(`search${paper.topic}${i}`)}>
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
                            
                        <tr onClick={() => toggleHidden(`search${paper.topic}${i}`)}>
                            <td style={{ display: showHidden[`search${paper.topic}${i}`] ? 'table-cell' : 'none'}} colSpan={2} className="research-hidden-row">
                                <p className="research-abstract">{paper.abstract}</p>
                                <p className="research-abstract">Topics: {paper.topic}</p>
                                <p className="research-abstract">Source: {paper.source}</p>
                            </td>
                        </tr>
                        </>
                    ))}
                </table>
            </div>
        )
    }
    // loading
    return (
        <h1 style={{ textAlign: "center"}}>Loading...</h1>
    );
}
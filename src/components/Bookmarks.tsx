import React, { FC, useState, useEffect } from 'react';
import { checkCookieExists } from '../utils/utils';

interface bookmarksI {
    data: string
}

export const Bookmarks: FC = () => {
    const [bookmarkData, setBookmarkData] = useState<bookmarksI>();
    var loggedIn: boolean = checkCookieExists("csrf_access_token") ? true : false;
 
    useEffect(() => {
        if (!loggedIn) return;
        const requestOptions = {
            method: "GET",
            headers: {"Content-Type": "application/json"}
        }
        fetch(`/api/bookmarks`, requestOptions)
        .then(response => response.json()).then(data => {
            setBookmarkData(data);
        })
        .catch((error) => {
            console.log(error);
        });
    }, [loggedIn]);

    if (!loggedIn) {
        return (<h1 className="info-h1">Create an account or login to view bookmarked papers</h1>);
    }
    else if (!bookmarkData) {
        return (<h1 className="info-h1">Loading...</h1>);
    }
    return (
        <div className="default-display-container">
            <h1>Bookmarks</h1>
            <p>{bookmarkData.data}</p>    
        </div>
    );
}
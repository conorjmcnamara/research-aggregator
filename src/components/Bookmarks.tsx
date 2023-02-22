import React, { FC, useState, useEffect } from 'react';
import { checkCookieExists } from '../utils/utils';

interface bookmarksI {
    data: string
}

export const Bookmarks: FC = () => {
    const [bookmarkData, setBookmarkData] = useState<bookmarksI>();
    var loggedIn: boolean = checkCookieExists("csrf_access_token") ? true : false;
 
    useEffect(() => {
        if (loggedIn) {
            fetch(`/api/bookmarks`, {
                method: "GET",
                headers: {"Content-Type": "application/json"}
            })
            .then(response => response.json()).then(data => {
                setBookmarkData(data);
            })
            .catch((error) => {
                console.log(error);
            });
        }
    }, [loggedIn]);

    // check if the user is logged in
    if (!loggedIn) {
        return (<h1 className="info-h1">Create an account or login to view bookmarked papers</h1>);
    }
    // load until the bookmark data is ready
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
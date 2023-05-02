import React, { FC } from 'react';
import { useSelector } from 'react-redux';
import { RootState } from '../store';

export const Account: FC = () => {
    var loginStatus = useSelector((state: RootState) => state.loginStatus.status);

    if (!loginStatus) {
        return (<h1 className="info-h1">Create an account or login to view account settings</h1>);
    }
    return (
        <div className="default-display-container">
            <h1>Account Settings</h1>
        </div>
    );
}
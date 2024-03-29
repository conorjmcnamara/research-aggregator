import React, { FC, useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useSelector, useDispatch } from 'react-redux';
import { setLoginCookie } from '../slices/loginCookieSlice';
import { RootState } from '../store';
import { responseMsgI } from '../utils/utils';
import Form from 'react-bootstrap/Form';
import Button from 'react-bootstrap/Button';

export const Account: FC = () => {
    const [currentUserEmail, setCurrentUserEmail] = useState<string>("");
    const [newUserEmail, setNewUserEmail] = useState<string>("");
    const [newUserPassword, setNewUserPassword] = useState<string>("");
    const [responseMsg, setResponseMsg] = useState<responseMsgI>();
    const navigate = useNavigate();
    const dispatch = useDispatch();
    var loginCookie = useSelector((state: RootState) => state.loginCookie.cookie);

    useEffect(() => {
        if (!loginCookie) return;
        const requestOptions = {
            method: "GET",
            headers: {"Content-Type": "application/json"}
        }
        fetch("/api/user", requestOptions)
        .then(response => response.json()).then(data => {
            setCurrentUserEmail(data);
        })
        .catch((error) => {
            setResponseMsg({responseMsg: "account details fetch unsuccessful"});
            console.log(error.message);
        });
    }, [])

    const updateEmail = async() => {
        if (!loginCookie) return;
        else if (newUserEmail === currentUserEmail) {
            setResponseMsg({responseMsg: "email update unsuccessful"});
            return;
        }
        const requestOptions = {
            method: "PUT",
            headers: {"Content-Type": "application/json",
            "X-CSRF-TOKEN": loginCookie},
            body: JSON.stringify({email: newUserEmail})
        }
        fetch("/api/user", requestOptions)
        .then(response => {
            if (response.status === 200) return response.json();
            throw new Error();
        })
        .then((data) => {
            dispatch(setLoginCookie());
            setCurrentUserEmail(newUserEmail);
            setResponseMsg({responseMsg: data.data});
        })
        .catch((error) => {
            setResponseMsg({responseMsg: "email update unsuccessful"});
            console.log(error.message);
        })
    }

    const updatePassword = async() => {
        if (!loginCookie) return;
        const requestOptions = {
            method: "PUT",
            headers: {"Content-Type": "application/json",
            "X-CSRF-TOKEN": loginCookie},
            body: JSON.stringify({password: newUserPassword})
        }
        fetch("/api/user", requestOptions)
        .then(response => {
            if (response.status === 200) return response.json();
            throw new Error();
        })
        .then((data) => {
            dispatch(setLoginCookie());
            setResponseMsg({responseMsg: data.data});
        })
        .catch((error) => {
            setResponseMsg({responseMsg: "password update unsuccessful"});
            console.log(error.message);
        })
    }

    const deleteAccount = async() => {
        if (!loginCookie) return;
        const requestOptions = {
            method: "DELETE",
            headers: {"Content-Type": "application/json",
            "X-CSRF-TOKEN": loginCookie},
        }
        fetch("/api/user", requestOptions)
        .then(response => {
            if (response.status === 200) return response.json();
            throw new Error();
        })
        .then((data) => {
            setResponseMsg({responseMsg: data.data});
            dispatch(setLoginCookie());
            navigate(`/`);
        })
        .catch((error) => {
            setResponseMsg({responseMsg: "account deletion unsuccessful"});
            console.log(error.message);
        })
    }

    if (!loginCookie) {
        return (<h1 className="info-h1">Create an account or login to view account settings</h1>);
    }
    else if (!currentUserEmail) {
        return (<h1 className="info-h1">Loading...</h1>);
    }
    return (
        <div className="default-display-container">
            <h1>Account Settings</h1>
            {currentUserEmail && <p>Your email: {currentUserEmail}</p>}
            <Form className="user-form">
                <Form.Group className="user-form-group">
                    <p>Update Email Address</p>
                    <Form.Control className="user-form-bar" placeholder="Enter new email" onChange={event => setNewUserEmail(event.target.value)} />
                </Form.Group>
                <Button className="user-form-button" onClick={() => updateEmail()}>Update email</Button>
                <Form.Group className="user-form-group">
                    <p>Update Password</p>
                    <Form.Control className="user-form-bar" placeholder="Enter new password" onChange={event => setNewUserPassword(event.target.value)} />
                </Form.Group>
                <Button className="user-form-button" onClick={() => updatePassword()}>Update password</Button>
            </Form>
            <p className="user-form-link" onClick={() => deleteAccount()}>Delete account</p>
            {responseMsg && <p>{responseMsg.responseMsg}</p>}
        </div>
    );
}
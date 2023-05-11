import React, { FC, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useSelector, useDispatch } from 'react-redux';
import { setLoginCookie } from '../slices/loginCookieSlice';
import { RootState } from '../store';
import { responseMsgI } from '../utils/utils';
import Form from 'react-bootstrap/Form';
import Button from 'react-bootstrap/Button';

export const SignUp: FC = () => {
    const [userEmail, setUserEmail] = useState<string>("");
    const [userPassword, setUserPassword] = useState<string>("");
    const [responseMsg, setResponseMsg] = useState<responseMsgI>();
    const navigate = useNavigate();
    const dispatch = useDispatch();
    var loginCookie = useSelector((state: RootState) => state.loginCookie.cookie);

    const signUp = async() => {
        const requestOptions = {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({email: userEmail, password: userPassword})
        }
        fetch("/api/signup", requestOptions)
        .then(response => {
            if (response.status === 201) return response.json();
            throw new Error();
        })
        .then((data) => {
            fetch("/api/login", requestOptions)
            .then(response => {
                if (response.status === 200) {
                    dispatch(setLoginCookie());
                    setResponseMsg({responseMsg: data.data});
                    navigate(`/bookmarks`);
                }
                else throw new Error();
            })
        })
        .catch((error) => {
            setResponseMsg({responseMsg: "signup unsuccessful"});
            console.log(error.message);
        })
    }

    if (loginCookie) {
        return (<h1 className="info-h1">Session is currently active...</h1>);
    }
    return (
        <div className="default-display-container">
            <h1>Sign Up</h1>
            <Form className="user-form">
                <Form.Group className="user-form-group">
                    <p>Email Address</p>
                    <Form.Control className="user-form-bar" placeholder="Enter email" onChange={event => setUserEmail(event.target.value)} />
                </Form.Group>
                <Form.Group className="user-form-group">
                    <p>Password</p>
                    <Form.Control className="user-form-bar" placeholder="Enter password" onChange={event => setUserPassword(event.target.value)} />
                </Form.Group>
                <Button className="user-form-button" onClick={() => signUp()}>Sign up</Button>
            </Form>
            <p className="user-form-link" onClick={() => navigate(`/login`)}>Already have an account? Login</p>
            {responseMsg && <p>Sign up {responseMsg.responseMsg}</p>}
        </div>
    );
}
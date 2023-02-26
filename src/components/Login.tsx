import React, { FC, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { getCookie } from '../utils/utils';
import Form from 'react-bootstrap/Form';
import Button from 'react-bootstrap/Button';
import 'bootstrap/dist/css/bootstrap.min.css';

interface loginI {
    login: string;
}

export const Login: FC = () => {
    const navigate = useNavigate();
    const [userEmail, setUserEmail] = useState<string>("");
    const [userPassword, setUserPassword] = useState<string>("");
    const [loginResponse, setLoginResponse] = useState<loginI>();
    var loggedIn: boolean = getCookie("csrf_access_token") ? true : false;

    const login = async() => {
        const requestOptions = {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({email: userEmail, password: userPassword})
        }
        fetch("/api/login", requestOptions)
        .then(response => {
            if (response.status === 200) return response.json();
            throw new Error();
        })
        .then((data) => {
            setLoginResponse(data);
            navigate(`/bookmarks`);
        })
        .catch((error) => {
            setLoginResponse({login: "unsccessful"});
            console.log(error);
        })
    }
    
    if (loggedIn) {
        return (<h1 className="info-h1">Session is currently active...</h1>);
    }
    return (
        <div className="default-display-container">
            <h1>Login</h1>
            <Form className="signup-form">
                <Form.Group>
                    <p>Email Address</p>
                    <Form.Control className="signup-bar" placeholder="Enter email" onChange={event => setUserEmail(event.target.value)} />
                </Form.Group>
                <Form.Group>
                    <p>Password</p>
                    <Form.Control className="signup-bar" placeholder="Enter password" onChange={event => setUserPassword(event.target.value)} />
                </Form.Group>
                <Button className="signup-button" onClick={() => login()}>Login</Button>
            </Form>
            <p className="signup-link" onClick={() => navigate(`/signup`)}>New user? Signup</p>
            {loginResponse && <p>Login {loginResponse.login}</p>}
        </div>
    );
}
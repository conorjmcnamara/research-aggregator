import React, { FC, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { checkCookieExists } from '../utils/utils';
import Form from 'react-bootstrap/Form';
import Button from 'react-bootstrap/Button';
import 'bootstrap/dist/css/bootstrap.min.css'

interface loginI {
    login: string;
}

export const Login: FC = () => {
    const navigate = useNavigate();
    const [userEmail, setUserEmail] = useState<string>("");
    const [userPassword, setUserPassword] = useState<string>("");
    const [loginResponse, setLoginResponse] = useState<loginI>();
    var loggedIn: boolean = checkCookieExists("csrf_access_token") ? true : false;

    const login = async() => {
        fetch("/api/login", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({email: userEmail, password: userPassword})
        })
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
    
    // check if the user is logged in
    if (loggedIn) {
        return (<h1 className="info-h1">Session is currently active...</h1>);
    }
    return (
        <div className="default-display-container">
            <h1>Login</h1>
            <Form className="navbar-form">
                <Form.Control className="navbar-search-bar" placeholder="Email" onChange={event => setUserEmail(event.target.value)} />
                <Form.Control className="navbar-search-bar"placeholder="Password" onChange={event => setUserPassword(event.target.value)} />
                <Button onClick={() => login()}>Login</Button>
            </Form>
            <p onClick={() => navigate(`/signup`)}>New user? Signup</p>
            {loginResponse && <p>Login {loginResponse.login}</p>}
        </div>
    );
}
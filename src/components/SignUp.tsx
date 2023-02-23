import React, { FC, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { checkCookieExists } from '../utils/utils';
import Form from 'react-bootstrap/Form';
import Button from 'react-bootstrap/Button';
import 'bootstrap/dist/css/bootstrap.min.css'

interface signUpI {
    signup: string;
}

export const SignUp: FC = () => {
    const navigate = useNavigate();
    const [userEmail, setUserEmail] = useState<string>("");
    const [userPassword, setUserPassword] = useState<string>("");
    const [signUpResponse, setSignUpResponse] = useState<signUpI>();
    var loggedIn: boolean = checkCookieExists("csrf_access_token") ? true : false;

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
            setSignUpResponse(data);
            fetch("/api/login", requestOptions)
            .then(response => {
                if (response.status === 200) navigate(`/bookmarks`)
                else throw new Error();
            })
        })
        .catch((error) => {
            setSignUpResponse({signup: "unsccessful"});
            console.log(error);
        })
    }

    if (loggedIn) {
        return (<h1 className="info-h1">Session is currently active...</h1>);
    }
    return (
        <div className="default-display-container">
            <h1>Sign Up</h1>
            <Form className="signup-form">
                <Form.Group>
                    <p>Email Address</p>
                    <Form.Control className="signup-bar" placeholder="Enter email" onChange={event => setUserEmail(event.target.value)} />
                </Form.Group>
                <Form.Group>
                    <p>Password</p>
                    <Form.Control className="signup-bar" placeholder="Enter password" onChange={event => setUserPassword(event.target.value)} />
                </Form.Group>
                <Button className="signup-button" onClick={() => signUp()}>Sign up</Button>
            </Form>
            <p className="signup-link" onClick={() => navigate(`/login`)}>Already have an account? Login</p>
            {signUpResponse && <p>Sign up {signUpResponse.signup}</p>}
        </div>
    );
}
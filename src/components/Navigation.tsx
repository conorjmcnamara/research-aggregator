import React, { FC, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useSelector, useDispatch } from 'react-redux';
import { setLoginCookie } from '../slices/loginCookieSlice';
import { RootState } from '../store';
import { topics } from '../utils/utils';
import Button from 'react-bootstrap/Button';
import Container from 'react-bootstrap/Container';
import Form from 'react-bootstrap/Form';
import Nav from 'react-bootstrap/Nav';
import Navbar from 'react-bootstrap/Navbar';

export const Navigation: FC = () => {
    const navigate = useNavigate();
    const [query, setQuery] = useState<string>("");
    const topicID: string[] = Object.keys(topics);
    const dispatch = useDispatch();
    var loginCookie = useSelector((state: RootState) => state.loginCookie.cookie);

    const logout = async() => {
        const requestOptions = {
            method: "POST",
            headers: {"Content-Type": "application/json"}
        }
        fetch("/api/logout", requestOptions)
        .then(response => {
            if (response.status === 200) {
                dispatch(setLoginCookie());
                navigate(`/`);
            }
            else throw new Error();
        })
        .catch((error) => {
            console.log(error.message);
        });
    }

    return (
        <div>
            <Navbar className="navbar" expand="lg">
                <Container fluid>
                    <Navbar.Brand className="navbar-title" onClick={() => navigate(`/`)} href="/">Research</Navbar.Brand>
                    <Form className="navbar-form">
                        <Form.Control className="navbar-search-bar" placeholder="Search papers" onChange={event => setQuery(event.target.value)} style={{width:"20em"}} />
                        <Button className="navbar-search-button" onClick={() => navigate(`/search/${query}`)}>Search</Button>
                    </Form>
                    
                    <Navbar.Toggle className="navbar-menu"/>
                    <Navbar.Collapse >
                    <Nav className="ms-auto" style={{marginLeft: "0"}}>
                        <Nav.Link onClick={() => navigate(`/bookmarks`)} href="/bookmarks" style={{color: "white"}}>Bookmarks</Nav.Link>
                        {loginCookie ? (
                            <React.Fragment>
                                <Nav.Link onClick={() => navigate(`/account`)} href="/account" style={{color: "white"}}>Account</Nav.Link>
                                <Nav.Link onClick={() => logout()} style={{color: "white"}}>Sign Out</Nav.Link>
                            </React.Fragment>
                        ) : 
                            <Nav.Link onClick={() => navigate(`/login`)} href="/login" style={{color: "white"}}>Sign In</Nav.Link>
                        }
                    </Nav>
                    </Navbar.Collapse>
                </Container>
            </Navbar>

            <div className="navigation-container">
                <div className="navigation-buttons">
                    <h1>Topics</h1>

                    <div className="navigation-desktop-buttons">
                        {topicID.map((id: string) => (
                            <button key={`${id}btn`} onClick={() => navigate(`/topic/${id}`)}>{topics[id]}</button>
                        ))}
                    </div>

                    <div className="navigation-mobile-buttons">
                        <select defaultValue={"default"}>
                            <option value="default" disabled>Select a topic</option>
                            {topicID.map((id: string) => (
                                <option key={`${id}btn`} value={id}>{topics[id]}</option>
                            ))}
                        </select>
                    </div>
                </div>
            </div>
        </div>
    );
}
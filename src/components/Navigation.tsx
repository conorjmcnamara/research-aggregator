import React, { FC, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { topicsI } from '../utils/utils';
import Button from 'react-bootstrap/Button';
import Container from 'react-bootstrap/Container';
import Form from 'react-bootstrap/Form';
import Nav from 'react-bootstrap/Nav';
import Navbar from 'react-bootstrap/Navbar';
import 'bootstrap/dist/css/bootstrap.min.css'

interface Props {
    topics: topicsI
}

export const Navigation: FC<Props> = ({topics}) => {
    const [query, setQuery] = useState<string>("");
    const navigate = useNavigate();
    const topicID: string[] = Object.keys(topics);

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
                        <Nav.Link onClick={() => navigate(`/sign-in`)} href="/sign-in" style={{color: "white"}}>Sign In</Nav.Link>
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
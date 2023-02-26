import React, { FC } from 'react';
import { BrowserRouter, Route, Routes } from "react-router-dom";
import { Home } from './components/Home';
import { Navigation } from './components/Navigation';
import { Login } from './components/Login';
import { SignUp } from './components/SignUp';
import { Bookmarks } from './components/Bookmarks';
import { DisplayTopic } from './components/DisplayTopic';
import { DisplaySearch } from './components/DisplaySearch';
import { NotFound } from './components/NotFound';
import './App.css';

const App: FC = () => {
  return (
    <div className="App">
      <BrowserRouter>
        <Navigation />
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/login" element={<Login />} />
            <Route path="/signup" element={<SignUp />} />
            <Route path="/bookmarks" element={<Bookmarks />} />
            <Route path="/topic/:id" element={<DisplayTopic />} />
            <Route path="/search/:query" element={<DisplaySearch />} />
            <Route path="*" element={<NotFound />} />
          </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;
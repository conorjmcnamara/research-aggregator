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
import { topics } from './utils/utils';
import './App.css';

const App: FC = () => {
  return (
    <div className="App">
      <BrowserRouter>
        <Navigation topics={topics} />
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/login" element={<Login />} />
            <Route path="/signup" element={<SignUp />} />
            <Route path="/bookmarks" element={<Bookmarks />} />
            <Route path="/topic/:id" element={<DisplayTopic topics={topics} />} />
            <Route path="/search/:query" element={<DisplaySearch topics={topics} />} />
            <Route path="*" element={<NotFound />} />
          </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;
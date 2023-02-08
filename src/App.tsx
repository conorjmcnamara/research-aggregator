import React, { FC } from 'react';
import { BrowserRouter, Route, Routes } from "react-router-dom";
import './App.css';
import { topics } from './utils/utils';
import { Home } from './components/Home';
import { Navigation } from './components/Navigation';
import { DisplayTopic } from './components/DisplayTopic';
import { DisplaySearch } from './components/DisplaySearch';
import { NotFound } from './components/NotFound';

const App: FC = () => {
  return (
    <div className="App">
      <BrowserRouter>
        <Navigation topics={topics} />
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/topic/:id" element={<DisplayTopic topics={topics} />} />
            <Route path="/search/:query" element={<DisplaySearch topics={topics} />} />
            <Route path="*" element={<NotFound />} />
          </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;
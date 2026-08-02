import React, { useState } from 'react'
import ChatInterface from './components/ChatInterface'
import Sidebar from './components/Sidebar'
import './App.css'

export default function App() {
  const [activePlugin, setActivePlugin] = useState(null)

  return (
    <div className="app">
      <Sidebar activePlugin={activePlugin} onSelectPlugin={setActivePlugin} />
      <main className="main">
        <header className="header">
          <div className="logo">
            <span className="logo-icon">◈</span>
            <span>LifeOS</span>
          </div>
          <div className="badge">Local-first · MCP Ready</div>
        </header>
        <ChatInterface activePlugin={activePlugin} />
      </main>
    </div>
  )
}

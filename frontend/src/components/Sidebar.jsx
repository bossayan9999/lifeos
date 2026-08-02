import React, { useEffect, useState } from 'react'
import axios from 'axios'
import './Sidebar.css'

const CATEGORIES = {
  enterprise: 'Enterprise Systems',
  specialized: 'Specialized Plugins',
}

export default function Sidebar({ activePlugin, onSelectPlugin }) {
  const [plugins, setPlugins] = useState([])

  useEffect(() => {
    axios.get('/api/v1/plugins')
      .then(r => setPlugins(r.data))
      .catch(() => {
        setPlugins([
          { name: 'crm', description: 'CRM bridge', category: 'enterprise', enabled: true },
          { name: 'project_mgmt', description: 'Project management', category: 'enterprise', enabled: true },
          { name: 'code_repo', description: 'Code repository', category: 'specialized', enabled: true },
          { name: 'analytics', description: 'Analytics', category: 'specialized', enabled: true },
          { name: 'obsidian', description: 'Obsidian vault', category: 'specialized', enabled: true },
        ])
      })
  }, [])

  const byCat = plugins.reduce((acc, p) => {
    (acc[p.category] = acc[p.category] || []).push(p)
    return acc
  }, {})

  return (
    <aside className="sidebar">
      <div className="sidebar-title">MCP Plugin Hub</div>
      <button
        className={`plugin-btn ${!activePlugin ? 'active' : ''}`}
        onClick={() => onSelectPlugin(null)}
      >
        Local Knowledge
      </button>

      {Object.entries(byCat).map(([cat, list]) => (
        <div key={cat} className="plugin-group">
          <div className="plugin-group-title">{CATEGORIES[cat] || cat}</div>
          {list.map(p => (
            <button
              key={p.name}
              className={`plugin-btn ${activePlugin === p.name ? 'active' : ''} ${!p.enabled ? 'disabled' : ''}`}
              onClick={() => p.enabled && onSelectPlugin(p.name)}
              title={p.description}
              disabled={!p.enabled}
            >
              {p.name}
            </button>
          ))}
        </div>
      ))}

      <div className="sidebar-footer">
        <small>Data stays local. External calls are read-only.</small>
      </div>
    </aside>
  )
}

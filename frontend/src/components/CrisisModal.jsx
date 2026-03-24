import { useState } from 'react';

export default function CrisisModal({ crisis, onClose }) {
  if (!crisis || !crisis.show_helplines) return null;

  return (
    <div className="crisis-overlay" onClick={onClose}>
      <div className="crisis-modal" onClick={e => e.stopPropagation()}>
        <div className="crisis-header">
          <span className="crisis-icon">🆘</span>
          <h2>You Are Not Alone</h2>
          <p>Help is available right now. Please reach out to any of these services.</p>
        </div>

        <div className="crisis-helplines">
          {(crisis.resources || []).map((r, i) => (
            <div key={i} className="crisis-helpline">
              <div className="helpline-info">
                <span className="helpline-name">{r.name}</span>
                <span className="helpline-country">{r.country} • {r.available}</span>
              </div>
              <a href={`tel:${r.number.replace(/\D/g, '')}`} className="helpline-number">
                📞 {r.number}
              </a>
            </div>
          ))}
        </div>

        <div className="crisis-footer">
          <p>💚 Your safety matters. A trained counselor can help you through this.</p>
          <button className="btn btn-outline" onClick={onClose}>I understand</button>
        </div>
      </div>
    </div>
  );
}

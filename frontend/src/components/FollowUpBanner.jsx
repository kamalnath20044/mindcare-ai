import { useState, useEffect } from 'react';
import { getFollowUps, markFollowUpRead } from '../api/client';
import { useAuth } from '../context/AuthContext';

export default function FollowUpBanner() {
  const { user } = useAuth();
  const [followup, setFollowup] = useState(null);
  const [dismissed, setDismissed] = useState(false);

  useEffect(() => {
    if (!user) return;
    const uid = user.user_id || user.id;
    getFollowUps(uid)
      .then(res => {
        const fu = res.data.new || (res.data.followups && res.data.followups[0]);
        if (fu) setFollowup(fu);
      })
      .catch(() => {});
  }, [user]);

  if (!followup || dismissed) return null;

  const priorityClass = followup.priority === 'high' ? 'alert-high' : followup.priority === 'low' ? 'alert-low' : 'alert-medium';
  const icon = followup.type === 'streak' ? '🔥' : followup.type === 'recommendation' ? '💡' : '👋';

  return (
    <div className={`alert-banner ${priorityClass}`} style={{ marginBottom: 16 }}>
      <span className="alert-icon">{icon}</span>
      <div className="alert-content">
        <p>{followup.message}</p>
        {followup.recommendation && (
          <p style={{ marginTop: 6, fontSize: '0.8rem', opacity: 0.85 }}>{followup.recommendation}</p>
        )}
      </div>
      <button className="alert-dismiss" onClick={() => {
        setDismissed(true);
        if (followup.id) markFollowUpRead(followup.id).catch(() => {});
      }}>✕</button>
    </div>
  );
}

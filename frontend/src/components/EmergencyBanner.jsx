export default function EmergencyBanner({ onClose }) {
  return (
    <div className="distress-banner">
      <h3>🚨 We're Concerned About You</h3>
      <p>
        Your message suggests you may be going through a very difficult time.
        Please know that you're not alone and professional help is available 24/7.
      </p>
      <div className="helplines">
        <span className="helpline">📞 iCall: 9152987821</span>
        <span className="helpline">📞 Vandrevala: 1860-2662-345</span>
        <span className="helpline">📞 AASRA: 91-22-27546669</span>
        <span className="helpline">📞 NIMHANS: 080-46110007</span>
      </div>
      {onClose && (
        <button className="btn btn-ghost btn-sm" onClick={onClose} style={{ marginTop: 12 }}>
          Dismiss
        </button>
      )}
    </div>
  );
}

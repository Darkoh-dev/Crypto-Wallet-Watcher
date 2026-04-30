import { useEffect, useState } from "react";
import "./App.css";



function App() {
  const [wallets, setWallets] = useState([]);
  const [loadError, setLoadError] = useState("");
  const [formData, setFormData] = useState({
    address: "",
    chain: "ethereum",
    label: "",
    notes: "",
  });
  const[submitError, setSubmitError] = useState("");

  useEffect(() => {
    async function loadWallets() {
      try {
        const response = await fetch("http://127.0.0.1:8000/wallets");

        if (!response.ok) {
          throw new Error("Could not load wallets.");
        }

        const data = await response.json();
        setWallets(data);
      } catch {
        setLoadError("Wallets could not be loaded.");
      } 
    }

    loadWallets();
  }, []);

  function handleInputChange(event) {
    const { name, value } = event.target;

    setFormData((currentFormData) => ({
      ...currentFormData,
      [name]: value,
    }));
  }

  async function handleAddWallet(event) {
    event.preventDefault();
    setSubmitError("");

    try {
      const response = await fetch("http://127.0.0.1:8000/wallets", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          address: formData.address,
          chain: formData.chain,
          label: formData.label,
          notes: formData.notes,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Wallet could not be added.");
      }

      setWallets((currentWallets) => [...currentWallets, data]);
      setFormData({
        address: "",
        chain: "ethereum",
        label: "",
        notes: "",
      });
    } catch (error) {
      setSubmitError(error.message);
    }
  }


  return (
    <main className="app-shell">
      <section className="app-header">
        <div>
          <p className="eyebrow">Crypto Wallet Watcher</p>
          <h1>Watch public wallet activity from one dashboard.</h1>
          <p className="header-copy">
            Add public crypto wallet addresses, label them, and prepare them for read-only activity tracking.
          </p>
        </div>
      </section>

      <section className="dashboard-grid">
        <form className="panel wallet-form" onSubmit={handleAddWallet}>
          <div className="panel-heading">
            <h2>Add Wallet</h2>
            <p>Start with an Ethereum address.</p>
          </div>

          <label>
            Wallet Address
            <input
              type="text"
              name="address"
              value={formData.address}
              onChange={handleInputChange}
              placeholder="0x..."
            />
          </label>

          <label>
            Chain
            <select name="chain" value={formData.chain} onChange={handleInputChange}>
              <option value="ethereum">Ethereum</option>
              <option value="bitcoin">Bitcoin</option>
              <option value="litecoin">Litecoin</option>
              <option value="dogecoin">Dogecoin</option>
            </select>
          </label>

          <label>
            Label
            <input
              type="text"
              name="label"
              value={formData.label}
              onChange={handleInputChange}
            />
          </label>

          <label>
            Notes
            <textarea
              name="notes"
              value={formData.notes}
              onChange={handleInputChange}
            />
          </label>

          {submitError && <p className="error-message">{submitError}</p>}

          <button type="submit">Add Wallet</button>
        </form>

        <section className="panel wallet-list">
          <div className="panel-heading">
            <h2>Watchlist</h2>
            <p>Saved wallets will appear here.</p>
          </div>

          {loadError && <p className="error-message">{loadError}</p>}

          {!loadError && wallets.length === 0 && (
            <div className="empty-state">
              <p>No Wallets added yet.</p>
            </div>
          )}

          {!loadError && wallets.length > 0 && (
            <div className="wallet-items">
              {wallets.map((wallet) => (
                <article className="wallet-item" key={wallet.id}>
                  <div>
                    <h3>{wallet.label}</h3>
                    <p>{wallet.address}</p>
                  </div>
                  <span>{wallet.chain}</span>
                </article>
              ))}
            </div>
          )}
        </section>
      </section>
    </main>
  );
}


export default App;
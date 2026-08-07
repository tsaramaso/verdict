<script lang="ts">
  import { goto } from '$app/navigation';
  
  let uuid = '';
  let error = '';
  let loading = false;
  
  async function handleLogin(e: Event) {
    e.preventDefault();
    loading = true;
    error = '';
    
    try {
      const { token } = await fetch('http://localhost:8000/users/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ uuid }),
      }).then(r => {
        if (!r.ok) throw new Error('Login failed');
        return r.json();
      });
      
      localStorage.setItem('auth_token', token);
      await goto('/game');
    } catch (err) {
      error = 'Unknown code. Check and try again.';
    } finally {
      loading = false;
    }
  }
</script>

<main>
  <div class="card">
    <h1>Verdict</h1>
    
    {#if error}
      <p class="error">{error}</p>
    {/if}
    
    <form on:submit={handleLogin}>
      <label for="uuid">Login code</label>
      <input
        type="text"
        id="uuid"
        bind:value={uuid}
        autocomplete="username"
        autocapitalize="off"
        autocorrect="off"
        spellcheck="false"
        required
        autofocus
        disabled={loading}
      />
      <button type="submit" disabled={loading}>
        {loading ? 'Logging in...' : 'Log in'}
      </button>
    </form>
  </div>
</main>

<style>
  main {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100vh;
    background: #f5f5f5;
  }
  
  .card {
    background: white;
    padding: 2rem;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    width: 100%;
    max-width: 400px;
  }
  
  h1 {
    text-align: center;
    margin-bottom: 1.5rem;
  }
  
  form {
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }
  
  label {
    font-weight: 500;
  }
  
  input {
    padding: 0.5rem;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 1rem;
  }
  
  button {
    padding: 0.5rem;
    background: #007bff;
    color: white;
    border: none;
    border-radius: 4px;
    font-weight: 500;
    cursor: pointer;
  }
  
  button:hover:not(:disabled) {
    background: #0056b3;
  }
  
  button:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
  
  .error {
    color: #d32f2f;
    font-size: 0.9rem;
  }
</style>
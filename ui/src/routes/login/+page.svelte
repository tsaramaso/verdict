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
      await goto('/home');
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
    background-color: var(--color-bg);
  }
  
  .card {
    background-color: var(--color-bg-card);
    padding: var(--spacing-xl);
    border-radius: var(--radius-md);
    box-shadow: var(--shadow-md);
    width: 100%;
    max-width: 400px;
  }
  
  h1 {
    text-align: center;
    margin-bottom: var(--spacing-lg);
    font-size: var(--font-size-xl);
    font-weight: var(--font-weight-bold);
  }
  
  form {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-md);
  }
  
  label {
    font-weight: var(--font-weight-medium);
  }
  
  input {
    padding: var(--spacing-sm);
    border: 1px solid var(--color-border);
    border-radius: var(--radius-sm);
    font-size: var(--font-size-base);
  }
  
  button {
    padding: var(--spacing-sm);
    background-color: var(--color-primary);
    color: white;
    border: none;
    border-radius: var(--radius-sm);
    font-weight: var(--font-weight-medium);
    cursor: pointer;
  }
  
  button:hover:not(:disabled) {
    background-color: var(--color-primary-dark);
  }
  
  button:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
  
  .error {
    color: var(--color-danger);
    font-size: var(--font-size-sm);
  }
</style>
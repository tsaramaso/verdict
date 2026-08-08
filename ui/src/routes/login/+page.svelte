<!-- ui/src/routes/login/+page.svelte -->
<script lang="ts">
  import { enhance } from '$app/forms';
  let isLoading = false;

  function handleSubmit() {
    isLoading = true;
  }
</script>

<main>
  <div class="card">
    <h1>Verdict</h1>
    <form method="POST" use:enhance={handleSubmit}>
      <label for="uuid">Login code</label>
      <input
        type="text"
        id="uuid"
        name="uuid"
        required
        disabled={isLoading}
        autocomplete="username"
        autocapitalize="off"
      />
      <button type="submit" disabled={isLoading}>
        {isLoading ? 'Logging in...' : 'Log in'}
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
</style>
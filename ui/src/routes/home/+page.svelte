<script lang="ts">
  import { goto } from '$app/navigation';
  
  async function logout() {
    localStorage.removeItem('auth_token');
    await goto('/login');
  }
</script>

<main>
  <h1>Game Page (WIP)</h1>
  <p>You're logged in! Token stored.</p>
  <button onclick={logout}>Logout</button>
</main>

<style>
  main {
    padding: 2rem;
  }
</style>
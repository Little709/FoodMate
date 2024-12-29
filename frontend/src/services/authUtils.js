export const fetchUserAccount = async () => {
  try {
    const token = localStorage.getItem("token");
    if (!token) {
      throw new Error("No token found");
    }
    const res = await fetch(`${API_BASE_URL}/management/account`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
    if (!res.ok) {
      throw new Error(`Failed to fetch user account: ${res.statusText}`);
    }
    return await res.json();
  } catch (err) {
    console.error(err);
    throw err;
  }
};

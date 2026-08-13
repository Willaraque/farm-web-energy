import { useCallback, useEffect, useMemo, useState } from "react";
import PropTypes from "prop-types";
import { VerifyToken } from "../../api/tokens";
import SpinnerLoader from "../../components/SpinnerLoader";
import { AuthContext } from "./auth-context";

const SESSION_KEY = "energy-session";

function readSession() {
  try {
    return JSON.parse(localStorage.getItem(SESSION_KEY)) || null;
  } catch {
    return null;
  }
}

export default function AuthProvider({ children }) {
  const [session, setSession] = useState(readSession);
  const [isLoading, setIsLoading] = useState(Boolean(session?.accessToken));

  const signOut = useCallback(() => {
    localStorage.removeItem(SESSION_KEY);
    setSession(null);
  }, []);

  useEffect(() => {
    if (!session?.accessToken) {
      setIsLoading(false);
      return;
    }
    VerifyToken()
      .then(({ data }) => {
        if (!data.valid) signOut();
      })
      .catch(signOut)
      .finally(() => setIsLoading(false));
  }, [session?.accessToken, signOut]);

  const saveUser = useCallback(({ data }) => {
    const next = {
      username: data.username,
      accessToken: data.access_token,
      id: data._id,
    };
    localStorage.setItem(SESSION_KEY, JSON.stringify(next));
    setSession(next);
  }, []);

  const value = useMemo(
    () => ({
      isAutenticated: Boolean(session?.accessToken),
      getAccesToken: () => session?.accessToken || null,
      getRefreshToken: () => session?.accessToken || null,
      getUser: () => session?.username || "",
      getIdMongo: () => session?.id || null,
      saveUser,
      signOuth: signOut,
    }),
    [session, saveUser, signOut],
  );

  if (isLoading) return <SpinnerLoader label="Verificando sesión" />;
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

AuthProvider.propTypes = { children: PropTypes.node.isRequired };

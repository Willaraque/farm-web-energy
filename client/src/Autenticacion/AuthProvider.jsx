import React from 'react';
import { useContext, createContext, useState, useEffect } from "react";
import PropTypes from 'prop-types';
import { VerifyToken, RefreshToken } from "../api/Tokens";
import SpinnerLoader from "../components/SpinnerLoader";


const AuthContext = createContext({
    isAutenticated: false,
    getAccesToken: () => { },
    saveUser: (userData) => { },
    getRefreshToken: () => { },
    getUser: () => { },
    getIdMongo: () => { },
    signOuth: () => { },
})

function AuthProvider({ children }) {
    // Your logic here
    const [isAutenticated, setIsAutenticated] = useState(false);
    const [accessToken, setAccessToken] = useState("");
    const [user, setUser] = useState("");
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        checkAuth();
    }, [])

    async function checkAuth() {
        const accessToken = getRefreshToken();
        if (accessToken) {
            try {
                const response = await VerifyToken(accessToken);
                if (response.data.valid) {
                    const username = getUsername();
                    setUser(username)
                    setIsAutenticated(true);
                    setIsLoading(false);
                }
                else {
                    const refreshResponse = await RefreshToken(token);
                    localStorage.removeItem('token')
                    if (refreshResponse) {
                        saveSessionInfo(refreshResponse.data.username, refreshResponse.data.access_token, refreshResponse.data._id);
                        setIsAutenticated(true);
                        setIsLoading(false);
                    }
                }
            } catch (error) {
                console.log('Error verificando el token:', error);
            }
        }
        setIsLoading(false);
    }


    function saveSessionInfo(username, accessToken, _id) {
        localStorage.setItem("token", JSON.stringify(accessToken));
        localStorage.setItem("_id", JSON.stringify(_id));
        localStorage.setItem("username", JSON.stringify(username));
        setAccessToken(accessToken);
        setUser(username);
        setIsAutenticated(true);
    }

    function getAccesToken() {
        return accessToken;
    }

    function getRefreshToken() {
        const tokenData = localStorage.getItem("token");
        if (tokenData) {
            const token = JSON.parse(tokenData);
            return token;
        }
        return null;
    }

    function getIdMongo() {
        const mongoID = localStorage.getItem("_id");
        if (mongoID) {
            const _id = JSON.parse(mongoID);
            return _id;
        }
        return null;
    }

    function getUsername() {
        const Username = localStorage.getItem("username");
        if (Username) {
            const username = JSON.parse(Username);
            return username;
        }
        return null;
    }

    function saveUser(userData) {
        saveSessionInfo(userData.data.username,
            userData.data.access_token,
            userData.data._id)
    }

    function getUser() {
        return user;
    }

    function signOuth() {
        setIsAutenticated(false);
        setAccessToken("");
        setUser("");
        localStorage.removeItem('token');
        localStorage.removeItem('_id');
        localStorage.removeItem('username');


    }

    return (
        <div>
            <AuthContext.Provider value={{
                isAutenticated,
                getAccesToken,
                saveUser,
                getRefreshToken,
                getUser,
                getIdMongo,
                signOuth,
            }}>
                {isLoading ? <SpinnerLoader /> : children}
            </AuthContext.Provider>
        </div>
    );
}

AuthProvider.propTypes = {
    children: PropTypes.node.isRequired
};

export default AuthProvider;

export const useAuth = () => useContext(AuthContext);
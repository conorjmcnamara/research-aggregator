import { createSlice } from '@reduxjs/toolkit';
import { getCookie } from '../utils/utils';

interface loginStateI {
    cookie: string | undefined
}

const initialState: loginStateI = {
    cookie: getCookie("csrf_access_token")
}

export const loginCookieSlice = createSlice({
    name: "login",
    initialState,
    reducers: {
        setLoginCookie: (state) => {
            state.cookie = getCookie("csrf_access_token")
        }
    }
})

export const {setLoginCookie} = loginCookieSlice.actions
export default loginCookieSlice.reducer
import { createSlice } from '@reduxjs/toolkit';
import { getCookie } from '../utils/utils';

interface loginStateI {
    status: string | undefined
}

const initialState: loginStateI = {
    status: getCookie("csrf_access_token")
}

export const loginStatusSlice = createSlice({
    name: "login",
    initialState,
    reducers: {
        setLoginStatus: (state) => {
            state.status = getCookie("csrf_access_token")
        }
    }
})

export const {setLoginStatus} = loginStatusSlice.actions
export default loginStatusSlice.reducer
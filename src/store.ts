import { configureStore } from '@reduxjs/toolkit';
import loginCookieReducer from './slices/loginCookieSlice';

export const store = configureStore({
    reducer: {
        loginCookie: loginCookieReducer
    }
});

export type RootState = ReturnType<typeof store.getState>
export type AppDispatch = typeof store.dispatch
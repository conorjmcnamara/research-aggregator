import { configureStore } from '@reduxjs/toolkit';
import loginReducer from './slices/loginStatusSlice';

export const store = configureStore({
    reducer: {
        loginStatus: loginReducer
    }
});

export type RootState = ReturnType<typeof store.getState>
export type AppDispatch = typeof store.dispatch
import { render, screen } from '@testing-library/react';
import { NotFound } from "../components/NotFound";
import '@testing-library/jest-dom';

test("NotFound component test", () => {
    render(<NotFound />);
    const text = screen.getByText(/404/i);
    expect(text).toBeInTheDocument();
})
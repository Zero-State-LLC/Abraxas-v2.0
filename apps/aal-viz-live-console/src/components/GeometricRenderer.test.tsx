import { render, screen } from "@testing-library/react";
import { GeometricRenderer } from "./GeometricRenderer";

describe("GeometricRenderer", () => {
  it("renders svg geometric path", () => {
    render(<GeometricRenderer data-testid="geo" />);
    expect(screen.getByTestId("geo").tagName.toLowerCase()).toBe("svg");
  });
});

"use client";

import Link from "next/link";
import { GL } from "./gl";
import { Pill } from "./pill";
import { Button } from "./ui/button";
import { useState } from "react";
import { useAuth } from "@/contexts/AuthContext";

export function Hero() {
  const [hovering, setHovering] = useState(false);
  const { isLoggedIn } = useAuth();

  return (
    <div className="flex flex-col h-svh justify-between">
      <GL hovering={hovering} />

      <div className="pb-16 mt-auto text-center relative">
        <Pill className="mb-6">AI POWERED</Pill>
        <h1 className="text-5xl sm:text-6xl md:text-7xl font-sentient">
          DS <br />
          <i className="font-light">MASKING AI</i>
        </h1>
        <p className="font-mono text-sm sm:text-base text-foreground/60 text-balance mt-8 max-w-[440px] mx-auto">
          Advanced NER and context-based detection to protect personal information
        </p>

        <Link className="contents max-sm:hidden" href={isLoggedIn ? "/dashboard" : "/#contact"}>
          <Button
            className="mt-14"
            onMouseEnter={() => setHovering(true)}
            onMouseLeave={() => setHovering(false)}
          >
            {isLoggedIn ? "[Dashboard]" : "[Contact Us]"}
          </Button>
        </Link>
        <Link className="contents sm:hidden" href={isLoggedIn ? "/dashboard" : "/#contact"}>
          <Button
            size="sm"
            className="mt-14"
            onMouseEnter={() => setHovering(true)}
            onMouseLeave={() => setHovering(false)}
          >
            {isLoggedIn ? "[Dashboard]" : "[Contact Us]"}
          </Button>
        </Link>
      </div>
    </div>
  );
}

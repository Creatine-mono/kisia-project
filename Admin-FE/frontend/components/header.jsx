"use client";

import Link from "next/link";
import { Logo } from "./logo";
import { MobileMenu } from "./mobile-menu";
import { useAuth } from "@/contexts/AuthContext";
import { useRouter } from "next/navigation";
import { Dialog, DialogContent, DialogTrigger, DialogTitle } from "@/components/ui/dialog";
import { LoginForm } from "./login-form";
import { SignupForm } from "./signup-form";
import { useState } from "react";

export const Header = () => {
  const { isLoggedIn, logout } = useAuth();
  const router = useRouter();
  const [loginOpen, setLoginOpen] = useState(false);
  const [showSignup, setShowSignup] = useState(false);

  const handleLogout = () => {
    logout();
    router.push("/");
  };

  return (
    <div className="fixed z-50 pt-8 md:pt-14 top-0 left-0 w-full">
      <header className="flex items-center justify-between container">
        <Link href="/">
          <Logo className="w-[100px] md:w-[120px]" />
        </Link>
        <nav className="flex max-lg:hidden absolute left-1/2 -translate-x-1/2 items-center justify-center gap-x-10">
          {["About", "Portfolio", "Insights", "Contact"].map((item) => (
            <Link
              className="uppercase inline-block font-mono text-foreground/60 hover:text-foreground/100 duration-150 transition-colors ease-out"
              href={`#${item.toLowerCase()}`}
              key={item}
            >
              {item}
            </Link>
          ))}
        </nav>
        <div className="flex max-lg:hidden items-center gap-x-6">
          {isLoggedIn ? (
            <button
              onClick={handleLogout}
              className="uppercase transition-colors ease-out duration-150 font-mono text-primary hover:text-primary/80"
            >
              Logout
            </button>
          ) : (
            <Dialog
              open={loginOpen}
              onOpenChange={(open) => {
                setLoginOpen(open);
                if (!open) setShowSignup(false);
              }}
            >
              <DialogTrigger asChild>
                <button className="uppercase transition-colors ease-out duration-150 font-mono text-primary hover:text-primary/80">
                  Sign In
                </button>
              </DialogTrigger>
              <DialogContent className="max-w-4xl">
                <DialogTitle className="sr-only">
                  {showSignup ? "회원가입" : "로그인"}
                </DialogTitle>
                {showSignup ? (
                  <SignupForm
                    onSuccess={() => setLoginOpen(false)}
                    onSwitchToLogin={() => setShowSignup(false)}
                  />
                ) : (
                  <LoginForm
                    onSuccess={() => setLoginOpen(false)}
                    onSwitchToSignup={() => setShowSignup(true)}
                  />
                )}
              </DialogContent>
            </Dialog>
          )}
        </div>
        <MobileMenu />
      </header>
    </div>
  );
};

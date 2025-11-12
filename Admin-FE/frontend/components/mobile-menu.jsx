"use client";

import { cn } from "@/lib/utils";
import * as Dialog from "@radix-ui/react-dialog";
import { Menu, X } from "lucide-react";
import Link from "next/link";
import { useState } from "react";
import { useAuth } from "@/contexts/AuthContext";
import { Dialog as LoginDialog, DialogContent, DialogTrigger, DialogTitle } from "@/components/ui/dialog";
import { LoginForm } from "./login-form";
import { SignupForm } from "./signup-form";


export const MobileMenu = ({ className }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [loginOpen, setLoginOpen] = useState(false);
  const [showSignup, setShowSignup] = useState(false);
  const { isLoggedIn } = useAuth();

  const menuItems = [
    { name: "About", href: "#about" },
    { name: "Portfolio", href: "#portfolio" },
    { name: "Insights", href: "#insights" },
    { name: "Contact", href: "#contact" },
  ];

  const handleLinkClick = () => {
    setIsOpen(false);
  };

  return (
    <Dialog.Root modal={false} open={isOpen} onOpenChange={setIsOpen}>
      <Dialog.Trigger asChild>
        <button
          className={cn(
            "group lg:hidden p-2 text-foreground transition-colors",
            className
          )}
          aria-label="Open menu"
        >
          <Menu className="group-[[data-state=open]]:hidden" size={24} />
          <X className="hidden group-[[data-state=open]]:block" size={24} />
        </button>
      </Dialog.Trigger>

      <Dialog.Portal>
        <div
          data-overlay="true"
          className="fixed z-30 inset-0 bg-black/50 backdrop-blur-sm"
        />

        <Dialog.Content
          onInteractOutside={(e) => {
            if (
              e.target instanceof HTMLElement &&
              e.target.dataset.overlay !== "true"
            ) {
              e.preventDefault();
            }
          }}
          className="fixed top-0 left-0 w-full z-40 py-28 md:py-40"
        >
          <Dialog.Title className="sr-only">Menu</Dialog.Title>

          <nav className="flex flex-col space-y-6 container mx-auto">
            {menuItems.map((item) => (
              <Link
                key={item.name}
                href={item.href}
                onClick={handleLinkClick}
                className="text-xl font-mono uppercase text-foreground/60 transition-colors ease-out duration-150 hover:text-foreground/100 py-2"
              >
                {item.name}
              </Link>
            ))}

            <div className="mt-6">
              {!isLoggedIn && (
                <LoginDialog
                  open={loginOpen}
                  onOpenChange={(open) => {
                    setLoginOpen(open);
                    if (!open) setShowSignup(false);
                  }}
                >
                  <DialogTrigger asChild>
                    <button className="inline-block text-xl font-mono uppercase text-primary transition-colors ease-out duration-150 hover:text-primary/80 py-2">
                      Sign In
                    </button>
                  </DialogTrigger>
                  <DialogContent className="max-w-4xl">
                    <DialogTitle className="sr-only">
                      {showSignup ? "회원가입" : "로그인"}
                    </DialogTitle>
                    {showSignup ? (
                      <SignupForm
                        onSuccess={() => {
                          setLoginOpen(false);
                          setIsOpen(false);
                        }}
                        onSwitchToLogin={() => setShowSignup(false)}
                      />
                    ) : (
                      <LoginForm
                        onSuccess={() => {
                          setLoginOpen(false);
                          setIsOpen(false);
                        }}
                        onSwitchToSignup={() => setShowSignup(true)}
                      />
                    )}
                  </DialogContent>
                </LoginDialog>
              )}
            </div>
          </nav>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  );
};

import SignIn from "@/app/(auth)/_components/sign-in";

export default function SignInPage() {
  return (
    <div className="bg-background flex min-h-screen w-full items-center justify-center md:px-4">
      <SignIn callbackURL="/" />
    </div>
  );
}

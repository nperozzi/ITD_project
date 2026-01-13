import SignUp from "@/app/(auth)/_components/sign-up";

export default function SignUpPage() {
  return (
    <div className="bg-background flex min-h-screen w-full items-center justify-center md:px-4">
      <SignUp callbackURL="/" />
    </div>
  );
}

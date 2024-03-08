import LoadingIcon from "./LoadingIcon";

const AttackLoading: React.FC = () => {
  return (
    <div className="flex flex-col min-h-screen bg-gradient-to-r from-black to-blue-950">
      <h1 className="text-white text-4xl font-bold text-center pt-20">Analysing Dataset...</h1>
      <div className="flex justify-center pt-16">
        <LoadingIcon size={"big"} />
      </div>
    </div>
  );
}

export default AttackLoading;
